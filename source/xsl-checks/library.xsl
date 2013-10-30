<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" indent="yes" omit-xml-declaration="yes"/>

  <xsl:template match="*">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="text()">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="/">
    <part>
      <part-title><xsl:apply-templates mode="part-title" /></part-title>
      <xsl:apply-templates/>
    </part>
  </xsl:template>

  <xsl:template name="createid">
    <xsl:param name="use-url-attribute" select="0"/>
    <xsl:param name="node" select="."/>

    <xsl:choose>
      <xsl:when test="$node/@id">
        <em><xsl:value-of select="$node/@id"/></em>
      </xsl:when>
      <xsl:otherwise>
        <xsl:choose>
          <xsl:when test="$node/title">
            <quote><xsl:value-of select="normalize-space($node/title)"/></quote>
          </xsl:when>
          <xsl:when test="$use-url-attribute = 1">
            <xsl:variable name="shortened">
              <xsl:choose>
                <xsl:when test="string-length(normalize-space($node/@url)) &gt; 50">
                  <xsl:value-of select="substring(normalize-space($node/@url), 1, 50)"/>…
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="normalize-space($node/@url)"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
            <quote><xsl:value-of select="$shortened"/></quote>
          </xsl:when>
          <xsl:otherwise>
            <xsl:variable name="shortened">
              <xsl:choose>
                <xsl:when test="string-length(normalize-space($node)) &gt; 50">
                  <xsl:value-of select="substring(normalize-space($node), 1, 50)"/>…
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="normalize-space($node)"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
            <quote><xsl:value-of select="$shortened"/></quote>
          </xsl:otherwise>
        </xsl:choose>
        <xsl:if test="$node/ancestor::*[@id]">
          (in <em><xsl:value-of select="$node/ancestor::*[@id][1]/@id"/></em>)
        </xsl:if>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>