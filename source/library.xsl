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
        <xsl:value-of select="$node/@id"/>
      </xsl:when>
      <xsl:when test="$node/title">
        <xsl:value-of select="normalize-space($node/title)"/>
      </xsl:when>
      <xsl:otherwise>
        "<xsl:value-of select="substring(normalize-space($node), 1, 50)"/>..."
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>