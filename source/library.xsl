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
    <xsl:param name="node" select="."/>

    <xsl:choose>
      <xsl:when test="$node/@id">
        <em><xsl:value-of select="$node/@id"/></em>
      </xsl:when>
      <xsl:when test="$node/title">
        <em><xsl:value-of select="normalize-space($node/title)"/></em>
      </xsl:when>
      <xsl:otherwise>
        <quote><xsl:value-of select="substring(normalize-space($node), 1, 50)"/>...</quote>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>